package com.orderSystem;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.HashMap;

@SpringBootApplication
public class OrderSystemApplication {
    public static void main(String[] args) {
        register();
        SpringApplication.run(OrderSystemApplication.class, args);
    }

    public static void register() {
        String port = System.getProperty("server.port");
        System.out.println(port);
        var values = new HashMap<String, String>() {{
            put("service", "orders");
            put ("address", "localhost:" + port);
        }};

        ObjectMapper objectMapper = new ObjectMapper();
        String requestBody = null;
        try {
            requestBody = objectMapper
                    .writeValueAsString(values);
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }

        HttpClient client = HttpClient.newHttpClient();
        assert requestBody != null;
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://gateway:4000/register"))
                .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                .build();

        HttpResponse<String> response = null;
        try {
            response = client.send(request, HttpResponse.BodyHandlers.ofString());
            System.out.println(response.body());
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}
