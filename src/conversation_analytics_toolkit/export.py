# (C) Copyright IBM Corp. 2019, 2020.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from string import punctuation
EN_PUNCTUATION = punctuation + '’'

def sanitize_text(text, remove_punctuation=True, lower=True, tokenize=True):
    text = text.strip()
    if lower:
        text = text.lower()
    # if tokenize:
    #     words = word_tokenize(text)
    # else:
    #     words = text.split()
    # if remove_punctuation:
    #     words = [word for word in words if word not in EN_PUNCTUATION]
    # return ' '.join(words)
    if remove_punctuation:
        text = text.translate(str.maketrans('', '', EN_PUNCTUATION))
    return text

def filter_sentences(sentences, sentence_with_count=None, min_complexity=-1, max_complexity=-1, min_confidence=-1,
                     max_confidence=-1, max_sentences_limit = None):
    result = []
    # apply filter based on complexity and confidence
    discarded = 0
    for index, sentence in sentences.iterrows():
        if min_complexity > 0 or max_complexity > 0:
            clean_sentence = sanitize_text(sentence['example'])
            complexity = len(clean_sentence.split())
            if min_complexity > 0 and complexity < min_complexity:
                discarded += 1
                continue
            if 0 < max_complexity < complexity:
                discarded += 1
                continue
        if min_confidence > 0:
            if sentence['confidence'] < min_confidence:
                discarded += 1
                continue
        if max_confidence > 0:
            if sentence['confidence'] > max_confidence:
                discarded += 1
                continue
        if sentence_with_count is not None:
            if sentence['example'] in sentence_with_count:
                sentence_with_count[sentence['example']] += 1
                discarded += 1
                continue

        result.append(sentence['example'])

        if max_sentences_limit:
            if len(result) == max_sentences_limit:
                logger.info("\tmax sentences limit reached. We will not consider any remaining examples/sentences")
                break

    return result
