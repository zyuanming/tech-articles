import unittest
import tempfile
from pathlib import Path
from exploration_scope import exploration_articles, supplementary_visuals, LEGACY_COLLECTION, SERIES_COLLECTION, DOOM_COLLECTION

class ScopeTests(unittest.TestCase):
    def legacy(self):
        return [{'id': 'old-'+str(i), 'collection': LEGACY_COLLECTION} for i in range(10)]
    def test_first_complete_continuation_keeps_all_ten(self):
        rows = self.legacy()+[{'id':'new-1','collection':SERIES_COLLECTION}, {'id':'unrelated'}]
        self.assertEqual([r['id'] for r in exploration_articles(rows)],
                         ['old-'+str(i) for i in range(10)]+['new-1'])
    def test_incremental_counts_are_derived(self):
        for count in (1,5,30):
            rows=self.legacy()+[{'id':'new-'+str(i),'collection':SERIES_COLLECTION} for i in range(count)]
            self.assertEqual(len(exploration_articles(rows)),10+count)
    def test_missing_old_article_fails(self):
        with self.assertRaises(ValueError):
            exploration_articles(self.legacy()[:-1]+[{'id':'new','collection':SERIES_COLLECTION}])
    def test_missing_continuation_fails(self):
        with self.assertRaises(ValueError): exploration_articles(self.legacy())
    def test_duplicate_selected_id_fails(self):
        with self.assertRaises(ValueError):
            exploration_articles(self.legacy()+[{'id':'old-0','collection':SERIES_COLLECTION}])
    def test_retains_catalog_order(self):
        rows=[{'id':'new-1','collection':SERIES_COLLECTION}]+self.legacy()
        self.assertEqual(exploration_articles(rows),rows)

class DoomScopeTests(unittest.TestCase):
    def base(self):
        return [{'id': 'legacy-'+str(i), 'collection': LEGACY_COLLECTION} for i in range(10)]+[{'id':'student-new', 'collection':SERIES_COLLECTION}]
    def test_every_published_doom_is_included_without_fixed_total(self):
        for count in (0,1,3,6):
            rows=self.base()+[{'id':'doom-'+str(i),'collection':DOOM_COLLECTION} for i in range(count)]+[{'id':'not-selected','collection':'other'}]
            self.assertEqual(exploration_articles(rows),rows[:-1])
    def test_cross_series_duplicate_is_rejected(self):
        with self.assertRaises(ValueError):
            exploration_articles(self.base()+[{'id':'student-new','collection':DOOM_COLLECTION}])
    def test_doom_does_not_replace_legacy_regression(self):
        with self.assertRaises(ValueError):
            exploration_articles(self.base()[1:]+[{'id':'doom-1','collection':DOOM_COLLECTION}])

class SupplementTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.directory=self.root/'articles'/'2026-10-12-sample';self.directory.mkdir(parents=True)
        self.item={'id':'2026-10-12-sample','path':'articles/2026-10-12-sample/read.md'}
        (self.directory/'read.md').write_text('# Test\n![body](body.png)\n')
        (self.directory/'body.png').write_bytes(b'fixture not executed as image')
    def tearDown(self): self.temp.cleanup()
    def test_no_extra_images(self):
        self.assertEqual(supplementary_visuals(self.root,self.item),{'pages':[],'unembedded_images':[]})
    def test_originals_but_not_code_or_pdf(self):
        for name in ['source.svg','original.PNG','data.json','paper.pdf']:(self.directory/name).write_bytes(b'x')
        result=supplementary_visuals(self.root,self.item)
        self.assertEqual([Path(x).name for x in result['unembedded_images']],['original.PNG','source.svg'])
    def test_appendix_count_does_not_double_count_images(self):
        (self.directory/'source-figures.md').write_text('# Originals\n![A](one.png)\n![A repeat](one.png)\n![B](two.jpg)')
        for name in ['one.png','two.jpg','extra.gif']:(self.directory/name).write_bytes(b'x')
        result=supplementary_visuals(self.root,self.item)
        self.assertEqual(result['pages'][0]['images'],3)
        self.assertEqual([Path(x).name for x in result['unembedded_images']],['extra.gif'])
    def test_encoded_image_name(self):
        (self.directory/'read.md').write_text('![A](a%20b.png#view)')
        (self.directory/'a b.png').write_bytes(b'x')
        self.assertEqual([Path(x).name for x in supplementary_visuals(self.root,self.item)['unembedded_images']],['body.png'])
    def test_external_reference_not_retrieved(self):
        (self.directory/'read.md').write_text('![A](https://example.invalid/private.png)')
        self.assertEqual(len(supplementary_visuals(self.root,self.item)['unembedded_images']),1)
    def test_path_escape_rejected(self):
        for item in [{'id':'../escape','path':'articles/../escape/read.md'},dict(self.item,path='../outside.md')]:
            with self.assertRaises(ValueError):supplementary_visuals(self.root,item)
    def test_image_escape_rejected(self):
        (self.directory/'read.md').write_text('![A](../../outside.png)')
        with self.assertRaises(ValueError):supplementary_visuals(self.root,self.item)
    def test_symlink_escape_rejected(self):
        outside=self.root/'outside.png';outside.write_bytes(b'x')
        (self.directory/'escape.png').symlink_to(outside)
        with self.assertRaises(ValueError):supplementary_visuals(self.root,self.item)
    def test_empty_appendix_rejected(self):
        (self.directory/'source-figures.md').write_text('# Empty')
        with self.assertRaises(ValueError):supplementary_visuals(self.root,self.item)
    def test_external_appendix_rejected(self):
        (self.directory/'source-figures.md').write_text('![A](https://example.invalid/a.png)')
        with self.assertRaises(ValueError):supplementary_visuals(self.root,self.item)

class ImageIndexTests(unittest.TestCase):
    def test_nested_and_escaped_alt_brackets(self):
        from index_articles import rendered_image_count
        self.assertEqual(rendered_image_count("![direction [student/project]](a.png)\n![escaped \\\\[label\\\\]](b.png)"),2)
    def test_reference_and_html_images(self):
        from index_articles import rendered_image_count
        self.assertEqual(rendered_image_count("![reference][pic]\n\n[pic]: a.png\n\n<img src='b.png' alt='raw'>"),2)
    def test_code_example_is_not_an_image(self):
        from index_articles import rendered_image_count
        self.assertEqual(rendered_image_count("\x60\x60\x60markdown\n![not rendered](x.png)\n\x60\x60\x60\n\n![real](y.png)"),1)
    def test_reindex_keeps_rendered_count(self):
        import json
        from index_articles import refresh
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);article=root/'articles'/'2026-10-12-nested-alt'
            article.mkdir(parents=True)
            (article/'read.md').write_text("# Test\n![direction [student/project]](a.png)\n")
            (article/'a.png').write_bytes(b"fixture")
            for _ in range(2):
                self.assertEqual(refresh(root),{'articles':1,'assets':1})
                self.assertEqual(json.loads((root/'catalog.json').read_text())[0]['images'],1)

if __name__=='__main__': unittest.main()

