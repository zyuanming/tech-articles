import unittest
import tempfile
from pathlib import Path
from exploration_scope import exploration_articles, supplementary_visuals, LEGACY_COLLECTION, SERIES_COLLECTION

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

if __name__=='__main__': unittest.main()
