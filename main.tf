terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "2.13.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_container" "sndsshist" {
  image = "sndsshist:latest"
  name = "sndsshist"
  restart = "always"
  # volumes {
  #   container_path = "/myapp"
  #   # replace the host_path with full path for your project directory starting from root directory /
  #   host_path = "/path/to/your/project/directory"
  #   read_only = false
  # }
  ports {
    internal = 5000
    external = 80
    # external = 5100
    # external = 5200
  }
}
