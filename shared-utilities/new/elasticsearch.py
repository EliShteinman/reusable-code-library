def prepare_for_elasticsearch(self, transcription_result, file_info):
    """מכין נתונים לElasticsearch עם חיפוש חכם"""

    documents = []
    segments = transcription_result['segments']
    full_text = transcription_result['full_text']

    for i, segment in enumerate(segments):
        # מידע בסיסי על הקטע
        doc = {
            # מטא-דטה של הקובץ
            'file_hash': transcription_result['file_hash'],
            'file_name': file_info.get('name'),
            'file_path': file_info.get('path'),
            'language': transcription_result['language'],
            'total_duration': segments[-1]['end'] if segments else 0,

            # מידע על הקטע הספציפי
            'segment_id': i,
            'start_time': segment['start'],
            'end_time': segment['end'],
            'duration': segment['end'] - segment['start'],

            # הטקסט של הקטע
            'text': segment['text'].strip(),

            # הקשר - קטעים שמסביב (למשפטים חתוכים!)
            'context_before': self._get_context_before(segments, i),
            'context_after': self._get_context_after(segments, i),
            'full_context': self._get_full_context(segments, i),

            # חיפוש מילים בודדות עם זמנים
            'words': [
                {
                    'word': word['word'],
                    'start': word['start'],
                    'end': word['end'],
                    'confidence': word.get('probability', 1.0)
                }
                for word in segment.get('words', [])
            ],

            # טקסט מלא (לחיפוש רחב)
            'full_document_text': full_text,

            # תגיות לחיפוש
            'timestamp': datetime.now(),
            'indexed_at': datetime.now().isoformat()
        }

        documents.append(doc)

    return documents


def _get_context_before(self, segments, current_index, context_size=2):
    """מחזיר קטעים לפני הקטע הנוכחי"""
    start_idx = max(0, current_index - context_size)
    before_segments = segments[start_idx:current_index]
    return ' '.join([seg['text'].strip() for seg in before_segments])


def _get_context_after(self, segments, current_index, context_size=2):
    """מחזיר קטעים אחרי הקטע הנוכחי"""
    end_idx = min(len(segments), current_index + context_size + 1)
    after_segments = segments[current_index + 1:end_idx]
    return ' '.join([seg['text'].strip() for seg in after_segments])


def _get_full_context(self, segments, current_index, context_size=2):
    """מחזיר הקשר מלא - לפני, הקטע הנוכחי, ואחרי"""
    before = self._get_context_before(segments, current_index, context_size)
    current = segments[current_index]['text'].strip()
    after = self._get_context_after(segments, current_index, context_size)

    return f"{before} {current} {after}".strip()