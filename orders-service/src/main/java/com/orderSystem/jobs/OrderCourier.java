package com.orderSystem.jobs;

import com.orderSystem.model.Order;
import com.orderSystem.service.OrderService;

import java.util.concurrent.TimeUnit;

public class OrderCourier extends Thread {
    String id;
    OrderService orderService;

    public OrderCourier(String id, OrderService orderService) {
        this.id = id;
        this.orderService = orderService;
    }

    public void run() {

        try {
            TimeUnit.SECONDS.sleep(10);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        orderService.changeState(Order.State.SHIPPED, id);
    }
}
