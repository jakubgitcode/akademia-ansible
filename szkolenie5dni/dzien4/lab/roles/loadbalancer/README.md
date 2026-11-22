# Rola loadbalancer

nginx przed serwerami aplikacji. Lista backendów powstaje z grupy inventory `loadbalancer_grupa_backendow`
(domyślnie `appservers`): adres IP każdego hosta z jego faktów i port `loadbalancer_port_backendow`.
Dodajesz serwer do grupy — po uruchomieniu playbooka load balancer sam go uwzględnia.

Wymaga faktów hostów z grupy backendów: w tym samym uruchomieniu najpierw play na tej grupie (z gather_facts).
