let current_material = 1;

document.getElementById("add_material").addEventListener("click", (event) => {
    event.preventDefault();

    current_material++;

    let new_material_block = document.createElement("div");
    new_material_block.classList = "material_block";
    new_material_block.id = `material_block_${current_material}`;

    let material_name_input = document.createElement("input");
    material_name_input.type = "text";
    material_name_input.id = `material_${current_material}`;
    material_name_input.name = `material_${current_material}`;
    material_name_input.setAttribute('list', 'materials');

    let material_count_input = document.createElement("input");
    material_count_input.type = "number";
    material_count_input.id = `material_${current_material}_count`;
    material_count_input.name = `material_${current_material}_count`;
    material_count_input.step = "any";

    document.getElementById("materials_block").append(new_material_block);
    document.getElementById(`material_block_${current_material}`).append(material_name_input);
    document.getElementById(`material_block_${current_material}`).append(material_count_input);

});