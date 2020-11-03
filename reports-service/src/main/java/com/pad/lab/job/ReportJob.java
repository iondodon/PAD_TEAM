package com.pad.lab.job;

import com.pad.lab.model.Report;
import com.pad.lab.repository.ReportRepo;
import lombok.SneakyThrows;
import org.quartz.JobDataMap;
import org.quartz.JobExecutionContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.quartz.QuartzJobBean;
import org.springframework.stereotype.Component;

import java.util.Random;
import java.util.Timer;
import java.util.TimerTask;

@Component
public class ReportJob extends QuartzJobBean {
    private static final Logger logger = LoggerFactory.getLogger(ReportJob.class);

    @Autowired
    ReportRepo reportRepo;

    private int timeOutCounterInSeconds = 0;
    private boolean isTimedOut = false;

    @Override
    protected void executeInternal(JobExecutionContext jobExecutionContext) {
        logger.info("Executing Job with key {}", jobExecutionContext.getJobDetail().getKey());

        JobDataMap jobDataMap = jobExecutionContext.getMergedJobDataMap();
        String reportType = jobDataMap.getString("reportType");
        String reportPath = jobDataMap.getString("reportPath");

        generateReport(reportType, reportPath);
    }

    private void generateReport(String reportType, String reportPath) {
        try {
            Report report1 = new Report();
            report1.setType(reportType);
            report1.setFileDownloadPath(reportPath);
            report1.setStatus("generating");
            Report savedReport = reportRepo.save(report1);
            logger.info("Generating Report of type {}", reportType);
            Timer timer = new Timer();
            timer.schedule(new TimerTask() {
                @SneakyThrows
                @Override
                public void run() {
                    if (timeOutCounterInSeconds == 5) {
                        savedReport.setStatus("timedOut");
                        reportRepo.save(savedReport);
                        isTimedOut = true;
                        throw new Exception("Timed out!");

                    }
                    timeOutCounterInSeconds++;

                }
            }, 0, 1000);
            Random random = new Random();
            Thread.sleep(random.ints(5, 7)
                    .findFirst()
                    .getAsInt() * 1000L);
            timer.cancel();
            if (!isTimedOut) {
                savedReport.setStatus("completed");
                reportRepo.save(savedReport);
            }
        } catch (
                Exception ex) {
            logger.error("Failed to generate report");
        }
    }
}
