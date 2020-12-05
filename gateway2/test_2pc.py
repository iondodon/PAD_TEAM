from two_phase_commit import TwoPhaseCommit

if __name__ == '__main__':
	print("Test 2Phase Commit 2PC")

	coordinator = TwoPhaseCommit()

	coordinator.perform(["http://google.com"])