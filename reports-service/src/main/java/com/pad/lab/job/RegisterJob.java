package com.pad.lab.job;

import org.quartz.JobExecutionContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.scheduling.quartz.QuartzJobBean;
import org.springframework.web.client.RestTemplate;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

public class RegisterJob extends QuartzJobBean {

    private static final Logger logger = LoggerFactory.getLogger(ReportJob.class);

    private void register() {
        final RestTemplate restTemplate = new RestTemplate();
        try {

            String port = System.getProperty("server.port");
            String registerAddress = "http://gateway:4000/register";
            String address = "localhost:" + port;
            // create headers
            HttpHeaders headers = new HttpHeaders();
            // set `content-type` header
            headers.setContentType(MediaType.APPLICATION_JSON);
            // set `accept` header
            headers.setAccept(Collections.singletonList(MediaType.APPLICATION_JSON));

            // create a map for post parameters
            Map<String, Object> map = new HashMap<>();
            map.put("address", address);
            map.put("service", "reports");

            // build the request
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(map, headers);

            // send POST request
            restTemplate.postForEntity(registerAddress, entity, String.class);
            logger.info("Registered!");
        } catch (Exception e) {
            logger.info("Service not registered!");
        }
    }

    @Override
    protected void executeInternal(JobExecutionContext jobExecutionContext) {
        logger.info("Executing Job with key {}", jobExecutionContext.getJobDetail().getKey());
        register();
    }
}
