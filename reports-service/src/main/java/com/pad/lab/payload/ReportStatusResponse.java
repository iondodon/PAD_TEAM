package com.pad.lab.payload;

import javax.validation.constraints.NotEmpty;

public class ReportStatusResponse {
    @NotEmpty
    private Long reportId;

    @NotEmpty
    private String reportType;

    @NotEmpty
    private String reportStatus;

    public Long getReportId() {
        return reportId;
    }

    public void setReportId(Long reportId) {
        this.reportId = reportId;
    }

    public String getReportStatus() {
        return reportStatus;
    }

    public void setReportStatus(String reportStatus) {
        this.reportStatus = reportStatus;
    }

    public String getReportType() {
        return reportType;
    }

    public void setReportType(String reportType) {
        this.reportType = reportType;
    }
}
