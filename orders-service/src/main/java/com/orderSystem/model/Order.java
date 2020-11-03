package com.orderSystem.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.ArrayList;
import java.util.List;

@Document(collection = "orders")
public class Order {
    @Id
    private String id;
    private float price;
    private String address;
    private ArrayList<String> products;
    private State state;

    public Order(){
    }

    public Order(float price, String address, ArrayList<String> products, State state) {
        this.price = price;
        this.address = address;
        this.products = products;
        this.state = state;
    }


    public void setId(String id) {
        this.id = id;
    }

    public void setPrice(float price) {
        this.price = price;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public void setProducts(ArrayList<String> products) {
        this.products = products;
    }

    public void setState(State state) {
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

    public State getState() {
        return state;
    }

    public String getId() { return id; }

    @Override
    public String toString() {
        return "Order{" +
                "id=" + id + '\'' +
                ", price='" + price + '\'' +
                ", address=" + address +
                ", products='" + products + '\'' +
                ", state=" + state +
                '}';
    }

    public enum State {
        PENDING("PENDING"),
        PROCESSING("PROCESSING"),
        SHIPPED("SHIPPED"),
        CANCELED("CANCELED");

        private String stateName;

        State(String state){
            this.stateName = state;
        }
    }

}
