package com.pad.lab;


import com.pad.lab.controller.ReportJobSchedulerController;
import org.quartz.JobDetail;
import org.quartz.Scheduler;
import org.quartz.Trigger;
import org.quartz.impl.StdSchedulerFactory;
import org.slf4j.Logger;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import static com.pad.lab.Utils.JobUtils.buildJobDetail;
import static com.pad.lab.Utils.JobUtils.buildJobTrigger;
import static org.slf4j.LoggerFactory.getLogger;

@SpringBootApplication
public class Lab1Application {

    private static final Logger logger = getLogger(ReportJobSchedulerController.class);


    public static void main(String[] args) {

        SpringApplication.run(Lab1Application.class, args);
        try {
            Scheduler scheduler = new StdSchedulerFactory().getScheduler();
            JobDetail jobDetail = buildJobDetail();
            Trigger trigger = buildJobTrigger(jobDetail);
            scheduler.start();
            scheduler.scheduleJob(jobDetail, trigger);
        } catch (Exception e) {

            logger.info("Register job error!");
        }
    }
}
