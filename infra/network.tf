# Create a VPC Network
resource "google_compute_network" "vpc" {
  name                    = "${var.application}-vpc"
  auto_create_subnetworks = false

#   depends_on = [
#     google_project_service.apis
#   ]
}

# Create a Private Subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.application}-subnet"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.10.0.0/24"
  private_ip_google_access = true

  depends_on = [
    google_compute_network.vpc,
  ]
}

resource "google_vpc_access_connector" "connector" {
  name          = var.application
  network       = google_compute_network.vpc.id
  region        = var.region
  ip_cidr_range = "10.100.0.0/28"
  min_instances = 2
  max_instances = 3

  depends_on = [
    google_compute_network.vpc,
    # google_project_service.apis
  ]
}

