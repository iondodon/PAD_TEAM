from two_phase_commit import TwoPhaseCommit

if __name__ == '__main__':
	print("Test 2Phase Commit 2PC")

	coordinator = TwoPhaseCommit()

	# coordinator.perform(["http://google.com"])
	coordinator.perform(["http://localhost:8001", "http://localhost:8000"])
