provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_compute_instance" "vm" {
  name         = "ai-cyber-vm"
  machine_type = "e2-standard-4"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose
    systemctl start docker
    systemctl enable docker

    # Clone your repo (update with your repo URL)
    cd /home/${var.vm_user}
    git clone https://github.com/k3v1n888/ai-cyber-platform.git
    cd ai-cyber-platform

    # Start Docker Compose stack (includes nginx + certbot)
    docker-compose up -d --build
  EOT

  service_account {
    email  = var.service_account_email
    scopes = ["cloud-platform"]
  }
}

resource "google_compute_firewall" "default" {
  name    = "allow-http-https"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8000"]
  }

  source_ranges = ["0.0.0.0/0"]
}

variable "project_id" {}
variable "region" {}
variable "zone" {}
variable "vm_user" {}
variable "service_account_email" {}