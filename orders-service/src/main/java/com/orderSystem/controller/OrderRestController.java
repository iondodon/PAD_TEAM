package com.orderSystem.controller;

import com.orderSystem.dto.OrderDTO;
import com.orderSystem.model.Order;
import com.orderSystem.service.OrderService;
import com.orderSystem.util.ObjectMapperUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/orders")

public class OrderRestController {

    @Autowired
    private OrderService orderService;

    @GetMapping(value = "/")
    public List<OrderDTO> getAllOrders(){
        return ObjectMapperUtils.mapAll(orderService.findAll(), OrderDTO.class);
    }

    @GetMapping(value = "/getOrderById/{id}")
    public OrderDTO getOrderById(@PathVariable("id") String id) {
        return ObjectMapperUtils.map(orderService.findOrderById(id), OrderDTO.class);
    }

    @GetMapping(value = "/getOrdersByState/{state}")
    public List<OrderDTO> getOrdersByState(@PathVariable("state") Order.State state){
        return ObjectMapperUtils.mapAll(orderService.findByState(state), OrderDTO.class);
    }

    @GetMapping(value = "/nrOfOrdersByState/{state}")
    public int getNrOfOrdersByState(@PathVariable("state") Order.State state){
        return ObjectMapperUtils.mapAll(orderService.findByState(state), OrderDTO.class).size();
    }

    @PostMapping(value = "/changeState/{id}/{state}")
    public ResponseEntity<?> changeOrderState(@PathVariable("state") Order.State state,@PathVariable("id") String id){
        if(orderService.changeState(state, id)) {
            return new ResponseEntity("Order's state changed successfully", HttpStatus.OK);
        } else {
            return new ResponseEntity("There is no order with such an ID", HttpStatus.OK);
        }
    }

    @PostMapping(value = "/")
    public ResponseEntity<?> saveOrUpdateOrder(@RequestBody OrderDTO orderDTO) {
        orderService.saveOrUpdateOrder(ObjectMapperUtils.map(orderDTO, Order.class));
        return new ResponseEntity("Order added/modified successfully", HttpStatus.OK);
    }

    @DeleteMapping(value = "/delete/{id}")
    public ResponseEntity<?> deleteById(@PathVariable String id) {
        Optional<Order> idOptional = orderService.findById(id);
        if(idOptional.isPresent()) {
            Order order = idOptional.get();
            orderService.deleteById(order.getId());
            return new ResponseEntity("Order deleted successfully", HttpStatus.OK);
        }
        else {
            return new ResponseEntity("Order was not found", HttpStatus.OK);
        }
    }



}
