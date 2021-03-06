from IPython import embed as shell

class Action(object):
    """
    An instantiated action stores the following.

    step_num: step number of this action in the plan
    name: name of this action
    active_timesteps: (start_time, end_time) for this action
    params: ordered list of Parameter objects
    preds: list of dictionaries where each dictionary contains information about
    a predicate. each dictionary contains
    - the Predicate object
    - negated (Boolean)
    - hl_info (string) which is "pre", "post" and "hl_state" if the predicate is
      a precondition, postcondition, or neither and part of the high level state
      respectively
    - active_timesteps (tuple of (start_time, end_time))
    """
    def __init__(self, step_num, name, active_timesteps, params, preds):
        self.step_num = step_num
        self.name = name
        self.active_timesteps = active_timesteps
        self.params = params
        self.preds = preds

    def __repr__(self):
        return "%d: %s %s %s"%(self.step_num, self.name, self.active_timesteps, " ".join([p.name for p in self.params]))

    def get_failed_preds(self, active_ts):
        failed = []
        for pred_d in self.preds:
            if pred_d['hl_info'] == 'hl_state': continue
            pred = pred_d['pred']
            negated = pred_d['negated']
            start, end = pred_d['active_timesteps']
            for t in range(max(start, active_ts[0]), 
                           min(end, active_ts[1])+1):
                if not pred.test(t, negated=negated):
                    failed.append((negated, pred, t))
        return failed

    def get_active_preds(self, t):
        res = []
        for pred_d in self.preds:
            if pred_d['hl_info'] == 'hl_state': continue
            start, end = pred_d['active_timesteps']
            if start <= t and end >= t: res.append(pred_d['pred'])
        return res

    def satisfied(self, active_ts):
        if self.active_timesteps[1] >= active_ts[0]:
            return True
        return len(self.get_failed_preds(active_ts)) == 0

    def first_failed_ts(self):
        start, end = self.active_timesteps
        ## init at the maximize
        t_min = end
        for b, p, t in self.get_failed_preds():
            if t < t_min:
                t_min = t
        return t_min
