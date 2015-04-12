float force_base_array[];

while(1)
{
    if(scan_has_ocurred())
    {
        add_item();
    }
    if(weight_event_has_ocurred())
    {
        remove_item();
    }
}


add_item()
{
    //force_base_array[];
    float new_force_values[] = calculate_force_values();
    float x = calculate_x(new_force_values);
    float y = calculate_y(new_force_values);
    float weight = calculate_weight(new_force_values);
    int quadrant = calculate_quadrant(x, y);
  
}
