import unittest
from exploration_scope import exploration_articles, LEGACY_COLLECTION, SERIES_COLLECTION

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
if __name__=='__main__': unittest.main()
