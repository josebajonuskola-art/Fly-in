from classes.config import Hub, Connection

# Hub parsing tests
print(Hub.model_validate("roof1 3 4 [zone=restricted color=red]"))
# print(Hub.model_validate("obstacleX 5 5"))
print(Hub.model_validate("corridorA 4 3 [max_drones=2]"))

# Connection parsing tests
print(Connection.model_validate("hub-roof1"))
# print(Connection.model_validate("hub- roof"))
print(Connection.model_validate("hub-roof333 [max_drones=2]"))
