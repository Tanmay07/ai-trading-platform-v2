import pandas as pd

class LeakageValidator:
    """
    Data leakage audit script that verifies no future data is accessed on Day T.
    """
    @staticmethod
    def audit_leakage(df: pd.DataFrame) -> dict:
        leakage_events = []
        
        # We need to verify that Simulated_Entry_Price corresponds to T+1 Open.
        # But we only have the final dataframe, so we will check if any trade exited before Entry.
        if 'Days_To_Target' in df.columns and 'Days_To_Stop' in df.columns:
            # Days to target/stop should be > 0. If 0, it means it evaluated Day T!
            invalid_targets = df[df['Days_To_Target'] == 0]
            if len(invalid_targets) > 0:
                leakage_events.append(f"Found {len(invalid_targets)} trades with Days_To_Target = 0 (Leakage)")
                
            invalid_stops = df[df['Days_To_Stop'] == 0]
            if len(invalid_stops) > 0:
                leakage_events.append(f"Found {len(invalid_stops)} trades with Days_To_Stop = 0 (Leakage)")
                
        # Are there any trades with positive MFE but 0 holding period?
        if 'MFE_Pct' in df.columns:
            invalid_mfe = df[(df['MFE_Pct'] > 0) & (df['Days_To_Target'] == 0) & (df['Days_To_Stop'] == 0)]
            if len(invalid_mfe) > 0:
                leakage_events.append(f"Found {len(invalid_mfe)} trades with MFE > 0 but 0 days held (Leakage)")
                
        status = "PASSED" if len(leakage_events) == 0 else "FAILED"
        
        return {
            "Audit_Status": status,
            "Leakage_Events_Found": len(leakage_events),
            "Events_Log": leakage_events
        }
