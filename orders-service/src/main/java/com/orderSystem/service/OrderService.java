package com.orderSystem.service;

import com.orderSystem.model.Order;
import org.springframework.http.ResponseEntity;

import java.util.List;
import java.util.Optional;

public interface OrderService {

    List<Order> findAll();

    Order findOrderById(String id);

    Optional<Order> findById(String id);

    Order saveOrUpdateOrder(Order order);

    void deleteById(String id);

    List<Order> findByState(Order.State state);

    boolean changeState(Order.State state, String id);

}
