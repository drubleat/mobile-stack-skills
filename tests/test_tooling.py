import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
validator = load('validate_skills')
installer = load('install_skills')

class ToolingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve() / 'repo'
        self.root.mkdir()
        for name in installer.SKILLS:
            shutil.copytree(ROOT / name, self.root / name)
        (self.root / 'README.md').write_text('Test repository')
        self.target = Path(self.tmp.name).resolve() / 'installed'

    def test_standalone_install_has_all_runtime_references(self):
        for name in installer.SKILLS:
            installer.install(self.target, [name], self.root)
            directory = self.target / name
            pending, visited = [directory / 'SKILL.md'], set()
            while pending:
                path = pending.pop()
                if path in visited:
                    continue
                visited.add(path)
                for link in validator.local_links(path, path.read_text()):
                    self.assertTrue(link.is_relative_to(directory), link)
                    self.assertTrue(link.exists(), link)
                    if link.suffix == '.md': pending.append(link)
            self.assertGreater(len(visited), 20)

    def test_collision_preflight_preserves_both_skills(self):
        existing = self.target / installer.SKILLS[1]
        existing.mkdir(parents=True)
        (existing / 'user-work').write_text('preserve')
        with self.assertRaises(FileExistsError):
            installer.install(self.target, list(installer.SKILLS), self.root)
        self.assertFalse((self.target / installer.SKILLS[0]).exists())
        self.assertEqual((existing / 'user-work').read_text(), 'preserve')

    def test_dangling_destination_symlink_is_not_overwritten(self):
        self.target.mkdir()
        dest = self.target / installer.SKILLS[0]
        dest.symlink_to(self.target / 'missing')
        with self.assertRaises(FileExistsError):
            installer.install(self.target, [installer.SKILLS[0]], self.root)
        self.assertTrue(dest.is_symlink())

    def test_copy_failure_rolls_back_only_new_installations(self):
        self.target.mkdir()
        (self.target / 'unrelated').write_text('keep')
        real_move = shutil.move
        count = 0
        def failing_move(*args, **kwargs):
            nonlocal count
            count += 1
            if count == 3: raise OSError('simulated full disk')
            return real_move(*args, **kwargs)
        with patch.object(installer.shutil, 'move', side_effect=failing_move):
            with self.assertRaises(OSError):
                installer.install(self.target, list(installer.SKILLS), self.root)
        self.assertEqual(list(self.target.iterdir()), [self.target / 'unrelated'])

    def test_reject_recursive_install_and_source_symlinks(self):
        name = installer.SKILLS[0]
        with self.assertRaises(ValueError):
            installer.install(self.root / name / 'nested', [name], self.root)
        (self.root / name / 'outside').symlink_to('/tmp')
        with self.assertRaises(ValueError):
            installer.install(self.target, [name], self.root)

    def test_current_tree_passes(self):
        errors, _ = validator.validate(ROOT)
        self.assertEqual(errors, [])

    def test_malformed_duplicate_and_broken_metadata_are_rejected(self):
        leaf = self.root / installer.SKILLS[0] / 'references/ai/guardrails.md'
        original = leaf.read_text()
        for replacement in ['title: bad: yaml', 'title: ok\ntitle: duplicate', 'title: 42']:
            with self.subTest(replacement=replacement):
                lines = original.splitlines()
                lines[1] = replacement
                leaf.write_text('\n'.join(lines))
                errors, _ = validator.validate(self.root)
                self.assertTrue(any(str(leaf) in e for e in errors))

    def test_broken_orphan_and_cross_skill_links_are_rejected(self):
        entry = self.root / installer.SKILLS[0] / 'SKILL.md'
        entry.write_text(entry.read_text() + '\n[missing](absent.md)\n[other](../supabase-postgres-best-practices/SKILL.md)\n')
        leaf = entry.parent / 'references/orphan.md'
        shutil.copyfile(entry.parent / 'references/ai/guardrails.md', leaf)
        errors, _ = validator.validate(self.root)
        for expected in ['broken local link', 'unreachable from SKILL.md', 'runtime reference requires another skill']:
            self.assertTrue(any(expected in e for e in errors), expected)

    def test_context_budget_and_ui_prompt_are_enforced(self):
        directory = self.root / installer.SKILLS[0]
        entry = directory / 'SKILL.md'
        entry.write_text(entry.read_text() + '\n' + 'filler ' * 700)
        agent = directory / 'agents/openai.yaml'
        agent.write_text(agent.read_text().replace('$mobile-stack-toolkit', 'something else'))
        errors, _ = validator.validate(self.root)
        self.assertTrue(any('context budget' in e for e in errors))
        self.assertTrue(any('default prompt' in e for e in errors))

    def test_fenced_examples_do_not_create_false_link_failures(self):
        entry = self.root / installer.SKILLS[0] / 'SKILL.md'
        entry.write_text(entry.read_text() + '\n```md\n[illustration](not-a-file.md)\n```\n')
        errors, _ = validator.validate(self.root)
        self.assertEqual(errors, [])

if __name__ == '__main__': unittest.main()
