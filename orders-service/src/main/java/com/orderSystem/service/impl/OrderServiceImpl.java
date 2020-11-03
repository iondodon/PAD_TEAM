package com.orderSystem.service.impl;

import com.orderSystem.jobs.OrderCourier;
import com.orderSystem.repository.OrderRepository;
import com.orderSystem.model.Order;
import com.orderSystem.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class OrderServiceImpl implements OrderService{

    @Autowired
    private OrderRepository orderRepository;

    @Override
    public List<Order> findAll() {
        return orderRepository.findAll();
    }


    @Override
    public Optional<Order> findById(String id) { return orderRepository.findById(id);}

    @Override
    public Order findOrderById(String id) { return orderRepository.findOrderById(id);}

    @Override
    public boolean changeState(Order.State state, String id) {
        Optional<Order> optionalOrder = orderRepository.findById(id);
        if(optionalOrder.isPresent()){
            Order order = optionalOrder.get();
            order.setState(state);
            orderRepository.save(order);
            if(order.getState().equals(Order.State.PROCESSING)) {
                OrderCourier courier = new OrderCourier(id, this);
                courier.start();
            }
            return true;
        }
        return false;
    }

    @Override
    public Order saveOrUpdateOrder(Order order) {
        return orderRepository.save(order);
    }

    @Override
    public void deleteById(String id) { orderRepository.deleteById(id); }

    @Override
    public List<Order> findByState(Order.State state) { return orderRepository.findByState(state); }

}
