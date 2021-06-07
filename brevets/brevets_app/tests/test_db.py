from acp_db import insert_time, get_times, clear_table
import nose
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)


# Times to test insertion for 
test_times = [
    {
        'index': '0',
        'miles': '0',
        'km': '0',
        'open': '2021-01-01T00:00',
        'close': '2021-01-01T01:00'
    },
    {
        'index': '1',
        'miles': '5',
        'km': '10',
        'open': '2021-01-01T01:23',
        'close': '2021-01-01T02:34'
    }
]


attributes = ['index', 'miles', 'km', 'open', 'close', '_id']


def test_one():
    clear_table()
    insert_time(test_times[0])

    db_found = get_times()
    result = {}
    for attr in attributes:
        result[attr] = db_found[0][attr]


    assert result == test_times[0]

def test_two():
    clear_table()
    for test in test_times:
        insert_time(test)
    
    db_found = get_times()
    result = []
    for i in range(len(test_times)):
        current = {}
        for attr in attributes:
            current[attr] = db_found[i][attr]
        result.append(current)

    assert result == test_times
