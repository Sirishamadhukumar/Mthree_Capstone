# Demo script

1. Run `python assignments/capstone/app.py --demo`.
2. Ask `How much is an international wire fee?` and verify FEES-001 and $40 appear.
3. Ask `What is the status of ACC-1001?` and verify status appears without account-holder PII.
4. Ask a branch approval policy question and check that source IDs are returned.
5. Set `GAMEDAY_FAULT=tool_outage` and repeat; confirm a degraded message and human handover. Clear the variable and verify recovery.
6. Run the autograder and inspect the audit/trace files.
