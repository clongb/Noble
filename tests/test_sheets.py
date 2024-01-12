import sheets

def test_get_values():
    assert sheets.get_values("Sheet1", "1JaCpF_APbGNrrNYeJhn6uQ3By68Dw2s_n7iDQknVtF4", "A1:C2") == [["1"],["2"],["3"],["4"],["5"],["6"]]

def test_write_to_sheet():
    sheets.write_to_sheet(tab="Sheet2", spreadsheet_id="1JaCpF_APbGNrrNYeJhn6uQ3By68Dw2s_n7iDQknVtF4", gid="1808144348", stage="RO32", slot="NM1",mapper="Greg",status="planning") 
    assert sheets.get_values("Sheet2", "1JaCpF_APbGNrrNYeJhn6uQ3By68Dw2s_n7iDQknVtF4", "C1:N1") == [["RO32"],["NM1"],["Greg"],[],[],[],[],[],[],[],[],["planning"]]

def test_remove_row():
    sheets.remove_row(tab="Sheet3", spreadsheet_id="1JaCpF_APbGNrrNYeJhn6uQ3By68Dw2s_n7iDQknVtF4", gid="2055370451", stage="RO32", slot="NM1",mapper="Greg")
    assert sheets.get_values("Sheet3", "1JaCpF_APbGNrrNYeJhn6uQ3By68Dw2s_n7iDQknVtF4", "C1:N1") == [[]]