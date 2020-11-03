package com.pad.lab.payload;

import javax.validation.constraints.NotEmpty;

public class ScheduleReportRequest {
    @NotEmpty
    private String reportType;
    @NotEmpty
    private String reportPath;

    private Integer jobPriority;

    public Integer getJobPriority() {
        return jobPriority;
    }

    public void setJobPriority(Integer jobPriority) {
        this.jobPriority = jobPriority;
    }

    public String getReportPath() {
        return reportPath;
    }

    public void setReportPath(String reportPath) {
        this.reportPath = reportPath;
    }

    public String getReportType() {
        return reportType;
    }

    public void setReportType(String reportType) {
        this.reportType = reportType;
    }
}
