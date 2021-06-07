from acp_times import close_time
import nose
import arrow
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)

start_time = arrow.get('2021-01-01T00:00:00')

# Test with 0 dist
def test_zero_dist():
    desired_time = start_time.shift(hours=+1)
    assert close_time(0, 200, start_time) == desired_time

# Test with two values less than 60km
def test_lt_sixty1():
    desired_time = start_time.shift(hours=+2)
    assert close_time(20, 200, start_time) == desired_time

def test_lt_sixty2():
    desired_time = start_time.shift(hours=+3)
    desired_time = desired_time.shift(minutes=+30)
    assert close_time(50, 200, start_time) == desired_time

# Test with two brevet distances with 200km checkpoint
def test_two_hundred1():
    desired_time = start_time.shift(hours=+13)
    desired_time = desired_time.shift(minutes=+30)
    assert close_time(200, 200, start_time) == desired_time

def test_two_hundred2():
    desired_time = start_time.shift(hours=+13)
    desired_time = desired_time.shift(minutes=+20)
    assert close_time(200, 300, start_time) == desired_time

# Test with two brevet distances with 300km checkpoint
def test_three_hundred1():
    desired_time = start_time.shift(hours=+20)
    assert close_time(300, 300, start_time) == desired_time

def test_three_hundred2():
    desired_time = start_time.shift(hours=+20)
    assert close_time(300, 400, start_time) == desired_time

# Test with two brevet distances with 400km checkpoint
def test_four_hundred1():
    desired_time = start_time.shift(hours=+27)
    assert close_time(400, 400, start_time) == desired_time

def test_four_hundred2():
    desired_time = start_time.shift(hours=+26)
    desired_time = desired_time.shift(minutes=+40)
    assert close_time(400, 600, start_time) == desired_time

# Test with two brevet distances with 600km checkpoint
def test_six_hundred1():
    desired_time = start_time.shift(hours=+40)
    assert close_time(600, 400, start_time) == desired_time

def test_six_hundred2():
    desired_time = start_time.shift(hours=+40)
    assert close_time(600, 1000, start_time) == desired_time

# Test with 1000km control point
def test_six_hundred1():
    desired_time = start_time.shift(hours=+75)
    assert close_time(1000, 1000, start_time) == desired_time
