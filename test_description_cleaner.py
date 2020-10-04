import unittest
import description_cleaner

NEW_LINE = "\r\n"


class TestDescriptionCleaner(unittest.TestCase):

    def test_empty_text(self):
        actual = description_cleaner.clean_description("")
        self.assertEqual("", actual)

    def test_plain_text(self):
        actual = description_cleaner.clean_description("Just some plain text")
        self.assertEqual("Just some plain text", actual)

    def test_repeated_text_1(self):
        actual = description_cleaner.clean_description(
            "https://www.amazon.co.uk/Inferno-Dante/dp/0385496982/ref=sr_1_7?s=books&ie=UTF8&qid=1513654376&sr=1-7&keywords=dante+inferno (https://www.amazon.co.uk/Inferno-Dante/dp/0385496982/ref=sr_1_7?s=books&ie=UTF8&qid=1513654376&sr=1-7&keywords=dante+inferno)")
        self.assertEqual(
            "https://www.amazon.co.uk/Inferno-Dante/dp/0385496982/ref=sr_1_7?s=books&ie=UTF8&qid=1513654376&sr=1-7&keywords=dante+inferno", actual)

    def test_repeated_text_2(self):
        actual = description_cleaner.clean_description(
            "http://www.websites.nl/ (http://www.websites.nl/)")
        self.assertEqual("http://www.websites.nl/", actual)

    def test_repeated_text_3(self):
        actual = description_cleaner.clean_description(
            "https://living-in-holland.nl/sites/ (https://living-in-holland.nl/sites/)")
        self.assertEqual("https://living-in-holland.nl/sites/", actual)

    def test_repeated_text_4(self):
        actual = description_cleaner.clean_description(
            "https://dutchreview.com/news/coronavirus-netherlands/ (https://dutchreview.com/news/coronavirus-netherlands/)")
        self.assertEqual(
            "https://dutchreview.com/news/coronavirus-netherlands/", actual)

    def test_repeated_text_with_extra_lines_1(self):
        actual = description_cleaner.clean_description(
            "pre amble (1)" + NEW_LINE +
            "https://www.government.nl/topics/coronavirus-covid-19/tackling-new-coronavirus-in-the-netherlands (https://www.government.nl/topics/coronavirus-covid-19/tackling-new-coronavirus-in-the-netherlands)" + NEW_LINE +
            "post amble (2)")
        self.assertEqual(
            "pre amble (1)" + NEW_LINE +
            "https://www.government.nl/topics/coronavirus-covid-19/tackling-new-coronavirus-in-the-netherlands" + NEW_LINE +
            "post amble (2)", actual)

    def test_repeated_text_with_other_1(self):
        actual = description_cleaner.clean_description(
            "(bad reviews) http://one.nl (http://one.nl)?")
        self.assertEqual("(bad reviews) http://one.nl?", actual)

# TODO xxx
# E-mail: info@crossfitninjas.nl (mailto:info@crossfitninjas.nl)
# E-mail: info@crossfitninjas.nl


if __name__ == '__main__':
    unittest.main()
