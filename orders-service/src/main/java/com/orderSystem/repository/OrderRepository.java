package com.orderSystem.repository;

import com.orderSystem.model.Order;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface OrderRepository extends MongoRepository<Order, String>{

    Optional<Order> findById(String id);

    Order findOrderById(String id);

    List<Order> findByState(Order.State state);

}
