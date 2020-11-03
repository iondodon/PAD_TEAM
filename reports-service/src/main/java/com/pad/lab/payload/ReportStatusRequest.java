package com.pad.lab.payload;

import javax.validation.constraints.NotEmpty;

public class ReportStatusRequest {
    @NotEmpty
    private String reportId;


    @NotEmpty
    private String reportStatus;

    public String getReportId() {
        return reportId;
    }

    public void setReportId(String reportId) {
        this.reportId = reportId;
    }

    public String getReportStatus() {
        return reportStatus;
    }

    public void setReportStatus(String reportStatus) {
        this.reportStatus = reportStatus;
    }

}
