"""Host doctor checks with simulated facts; not a real cloud-server acceptance."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location('b08_host_doctor', Path(__file__).resolve().parents[1] / 'doctor.py')
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


class DoctorTests(unittest.TestCase):
    def exercise(self, memory=3.5, cpus=2, disk=68.5, failed_tool=None,
                 permission_denied=False, identity=True, system='Linux'):
        calls = []
        tool_commands = {tuple(command): name for name, command, _ in doctor.TOOLS}

        def fake_sh(command):
            calls.append(command)
            if command[:3] == ['git', 'config', '--local']:
                values = {'user.name': '241880546', 'user.email': '241880546@localhost'}
                return (0, values[command[-1]]) if identity else (1, '')
            if command == ['git', 'config', '--global', 'user.name']:
                return 1, ''
            if command == ['docker', 'info', '--format', '{{json .RegistryConfig.Mirrors}}']:
                return 0, '["https://registry-mirror.example"]'
            name = tool_commands.get(tuple(command))
            if name is None:
                raise AssertionError('Unexpected command: {!r}'.format(command))
            if name == failed_tool:
                return 1, 'permission denied' if permission_denied else 'not found'
            return 0, name + ' test-version'

        fake_os = SimpleNamespace(cpu_count=lambda: cpus,
                                  path=SimpleNamespace(isdir=lambda _: True, exists=lambda _: False))
        fake_platform = SimpleNamespace(system=lambda: system, node=lambda: 'doctor-unit-test',
                                        release=lambda: 'test-kernel', machine=lambda: 'x86_64')
        fake_shutil = SimpleNamespace(disk_usage=lambda _: SimpleNamespace(free=int(disk * 2**30)))
        with tempfile.TemporaryDirectory(prefix='b08-doctor-test-') as directory:
            output = Path(directory) / 'new-evidence/env.json'
            stdout = io.StringIO()
            with patch.object(doctor, 'os', fake_os), patch.object(doctor, 'platform', fake_platform), \
                    patch.object(doctor, 'shutil', fake_shutil), patch.object(doctor, 'mem_gib', return_value=memory), \
                    patch.object(doctor, 'os_release', return_value='Simulated Linux'), \
                    patch.object(doctor, 'sh', side_effect=fake_sh), \
                    patch.object(sys, 'argv', ['doctor.py', '--out', str(output)]), \
                    contextlib.redirect_stdout(stdout):
                with self.assertRaises(SystemExit) as ended:
                    doctor.main()
            saved = json.loads(output.read_text(encoding='utf-8'))
            printed, _ = json.JSONDecoder().raw_decode(stdout.getvalue())
            self.assertEqual(saved, printed)
            return ended.exception.code, saved, stdout.getvalue(), calls

    def test_only_minimum_memory_is_adapted(self):
        self.assertEqual(doctor.MIN, {'cpus': 2, 'mem_gib': 3.5, 'disk_gib': 40})
        self.assertEqual(doctor.REC, {'cpus': 4, 'mem_gib': 8, 'disk_gib': 100})

    def test_memory_at_3_5_gib_passes_and_keeps_actual_measurement(self):
        code, env, _, _ = self.exercise(memory=3.5)
        self.assertEqual(code, 0)
        self.assertEqual(env['problems'], [])
        self.assertEqual(env['spec']['mem_gib'], 3.5)
        self.assertTrue(any('mem_gib=3.5' in text for text in env['warnings']))

    def test_memory_below_3_5_gib_still_fails(self):
        code, env, _, _ = self.exercise(memory=3.4)
        self.assertEqual(code, 1)
        self.assertTrue(any('mem_gib=3.4' in text and '3.5' in text for text in env['problems']))

    def test_memory_above_minimum_passes(self):
        code, env, _, _ = self.exercise(memory=4)
        self.assertEqual(code, 0)
        self.assertEqual(env['problems'], [])

    def test_memory_at_recommendation_has_no_memory_warning(self):
        code, env, _, _ = self.exercise(memory=8)
        self.assertEqual(code, 0)
        self.assertFalse(any('mem_gib' in text for text in env['warnings']))

    def test_cpu_minimum_is_not_relaxed(self):
        code, env, _, _ = self.exercise(cpus=1)
        self.assertEqual(code, 1)
        self.assertTrue(any('cpus=1' in text for text in env['problems']))

    def test_disk_minimum_is_not_relaxed(self):
        code, env, _, _ = self.exercise(disk=39.9)
        self.assertEqual(code, 1)
        self.assertTrue(any('disk_gib=39.9' in text for text in env['problems']))

    def test_all_resource_minima_are_inclusive(self):
        code, env, _, _ = self.exercise(cpus=2, memory=3.5, disk=40)
        self.assertEqual(code, 0)
        self.assertEqual(env['problems'], [])

    def test_recommendation_warnings_do_not_fail_small_sample(self):
        code, env, stdout, _ = self.exercise(cpus=2, memory=3.5, disk=68.5)
        self.assertEqual(code, 0)
        self.assertEqual(env['problems'], [])
        self.assertEqual(len(env['warnings']), 3)
        self.assertIn('环境自检：通过', stdout)

    def test_each_required_tool_is_still_required(self):
        for name in ['docker', 'compose', 'git', 'make', 'python3']:
            with self.subTest(tool=name):
                code, env, _, _ = self.exercise(failed_tool=name)
                self.assertEqual(code, 1)
                self.assertTrue(any(name in text for text in env['problems']))
                self.assertIsNone(env['tools'][name])

    def test_docker_permission_error_still_fails(self):
        code, env, _, _ = self.exercise(failed_tool='docker', permission_denied=True)
        self.assertEqual(code, 1)
        self.assertTrue(any('当前用户无权访问 Docker' in text for text in env['problems']))

    def test_optional_buildx_missing_only_warns(self):
        code, env, _, _ = self.exercise(failed_tool='buildx')
        self.assertEqual(code, 0)
        self.assertEqual(env['problems'], [])
        self.assertTrue(any('buildx' in text for text in env['warnings']))

    def test_missing_git_identity_still_fails(self):
        code, env, _, _ = self.exercise(identity=False)
        self.assertEqual(code, 1)
        self.assertTrue(any('本仓库未设置提交身份' in text for text in env['problems']))

    def test_non_linux_system_still_fails(self):
        code, env, _, _ = self.exercise(system='Windows')
        self.assertEqual(code, 1)
        self.assertTrue(any('不是 Linux' in text for text in env['problems']))

    def test_git_config_commands_are_read_only(self):
        _, _, _, calls = self.exercise()
        actual = [command for command in calls if command[:2] == ['git', 'config']]
        self.assertEqual(actual, [
            ['git', 'config', '--local', 'user.name'],
            ['git', 'config', '--local', 'user.email'],
            ['git', 'config', '--global', 'user.name'],
        ])


if __name__ == '__main__':
    unittest.main()
