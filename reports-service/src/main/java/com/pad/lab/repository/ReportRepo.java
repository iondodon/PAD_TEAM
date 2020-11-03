package com.pad.lab.repository;

import com.pad.lab.model.Report;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository("reportRepository")
public interface ReportRepo extends JpaRepository<Report, Long> {
}
