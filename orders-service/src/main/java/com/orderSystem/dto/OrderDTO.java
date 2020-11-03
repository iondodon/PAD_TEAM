package com.orderSystem.dto;

import com.orderSystem.model.Order;

import java.util.ArrayList;

public class OrderDTO {

    private String id;
    private float price;
    private String address;
    private ArrayList<String> products;
    private Order.State state;

    public OrderDTO(){

    }

    public OrderDTO(float price, String address, ArrayList<String> products, Order.State state) {
        this.price = price;
        this.address = address;
        this.products = products;
        this.state = state;
    }

    public String getId() {
        return id;
    }

    public void setPrice(float price) {
        this.price = price;
    }

    public void setId(String id) {
        this.id = id;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public void setProducts(ArrayList<String> products) {
        this.products = products;
    }

    public void setState(Order.State state) {
        this.state = state;
    }

    public float getPrice() {
        return price;
    }

    public String getAddress() {
        return address;
    }

    public ArrayList<String> getProducts() {
        return products;
    }

    public Order.State getState() {
        return state;
    }
}
