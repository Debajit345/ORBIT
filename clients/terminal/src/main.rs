fn main() {
    println!("ORBIT terminal client");
    println!("Runtime: {}", orbit_runtime::runtime_name());
    println!("Index: {}", orbit_index::engine_name());
    println!("Search: {}", orbit_search::engine_name());
    println!("Platform: {}", orbit_native::platform_name());
}