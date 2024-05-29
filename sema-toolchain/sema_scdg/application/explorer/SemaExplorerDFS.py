#!/usr/bin/env python3
import monkeyhex  # this will format numerical results in hexadecimal
import logging
import sys
from SemaExplorer import SemaExplorer
import os

log_level = os.environ["LOG_LEVEL"]
log = logging.getLogger("SemaExplorerDFS")
log.setLevel(log_level)

class SemaExplorerDFS(SemaExplorer):
    def __init__(
        self,
        simgr,
        exp_dir,
        nameFileShort,
        scdg_graph,
        call_sim
    ):
        super(SemaExplorerDFS, self).__init__(
            simgr,
            exp_dir,
            nameFileShort,
            scdg_graph,
            call_sim
        )
        self.config_logger()

    def config_logger(self):
        self.log_level = log_level
        self.log = log

    def step(self, simgr, stash="active", **kwargs):
        try:
            simgr = simgr.step(stash=stash, **kwargs)
        except Exception as inst:
            self.log.warning("ERROR IN STEP() - YOU ARE NOT SUPPOSED TO BE THERE !")
            # self.log.warning(type(inst))    # the exception instance
            self.log.warning(inst)  # __str__ allows args to be printed directly,
            exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.log.warning(exc_type, exc_obj)
            exit(-1)

        self.build_snapshot(simgr)

        if (len(self.fork_stack) > 0 or len(simgr.deadended) > self.deadended):
            self.log.info("A new block of execution have been executed with changes in sim_manager.")
            self.log.info("Currently, simulation manager is :\n" + str(simgr))
            self.log.info("pause stash len :" + str(len(simgr.stashes["pause"])))

        if len(self.fork_stack) > 0:
            self.log.info("fork_stack : " + str(len(self.fork_stack)) + " " + hex(simgr.active[0].addr) + " " + hex(simgr.active[1].addr))

        # We detect fork for a state
        self.manage_fork(simgr)

        # Remove state which performed more jump than the limit allowed
        super().remove_exceeded_jump(simgr)

        # Manage ended state
        super().manage_deadended(simgr)

        # If limit of simultaneous state is not reached and we have some states available in pause stash
        if len(simgr.stashes["pause"]) > 0 and len(simgr.active) < self.max_simul_state:
            moves = min(
                self.max_simul_state - len(simgr.active),
                len(simgr.stashes["pause"]),
            )
            for m in range(moves):
                self.take_longuest(simgr, "pause")

        super().drop_excessed_loop(simgr)
        # If states end with errors, it is often worth investigating. Set DEBUG_ERROR to live debug
        # TODO : add a log file if debug error is not activated
        super().manage_error(simgr)

        super().manage_unconstrained(simgr)

        for vis in simgr.active:
            self.dict_addr_vis.add(str(super().check_constraint(vis, vis.history.jump_target)))

        super().excessed_step_to_active(simgr)

        super().excessed_loop_to_active(simgr)

        self.time_evaluation(simgr)

        return simgr
