from acp_times import open_time
import nose
import arrow
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)

start_time = arrow.get('2021-01-01T00:00:00')

# Test with 0km control point
def test_zero_dist():
    assert open_time(0, 200, start_time) == start_time

# Test with 200km control point
def test_two_hundred():
    desired_time = start_time.shift(hours=+5)
    desired_time = desired_time.shift(minutes=+53)
    assert open_time(200, 200, start_time) == desired_time

# Test with 400km control point
def test_four_hundred():
    desired_time = start_time.shift(hours=+12)
    desired_time = desired_time.shift(minutes=+8)
    assert open_time(400, 400, start_time) == desired_time

# Test with 600km control point
def test_six_hundred():
    desired_time = start_time.shift(hours=+18)
    desired_time = desired_time.shift(minutes=+48)
    assert open_time(600, 600, start_time) == desired_time

# Test with 1000km control point
def test_one_thousand():
    desired_time = start_time.shift(hours=+33)
    desired_time = desired_time.shift(minutes=+5)
    assert open_time(1000, 1000, start_time) == desired_time