
def make_clean_hist(original_hist, name):

    new_hist = original_hist.Clone(name)
    new_hist.Reset()
    return new_hist

class up_down:
    up=0
    down=1
