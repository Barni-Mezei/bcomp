document.documentElement.style.cssText = "--main-background-color: red";

let address_line_container = document.getElementById("address_line");

for (let address = 0; address < RAM_SIZE; address++) {
    if (address % 100 == 0) {
        let new_address = document.createElement("p");
        new_address.classList = "address";
        new_address.textContent = address;
        address_line_container.appendChild(new_address);
    }
}