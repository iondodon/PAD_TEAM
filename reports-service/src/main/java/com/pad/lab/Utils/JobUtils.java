package com.pad.lab.Utils;

import com.pad.lab.job.RegisterJob;
import org.quartz.*;

import java.util.Date;
import java.util.UUID;

public class JobUtils {
    public static JobDetail buildJobDetail() {
        JobDataMap jobDataMap = new JobDataMap();

        return JobBuilder.newJob(RegisterJob.class).withIdentity(UUID.randomUUID().toString(), "register-jobs")
                .withDescription("Send Register Job").usingJobData(jobDataMap).storeDurably().build();
    }

    public static Trigger buildJobTrigger(JobDetail jobDetail) {
        return TriggerBuilder.newTrigger().forJob(jobDetail)
                .withIdentity(jobDetail.getKey().getName(), "register-triggers").withDescription("Send Register Trigger")
                .startAt(new Date())
                .withSchedule(SimpleScheduleBuilder.simpleSchedule().withMisfireHandlingInstructionFireNow()).build();
    }
}
