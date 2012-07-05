In this directory, there are three different deployments:
 - consumer
 - provider1
 - provider2


They will be launched and act independently. These is a list of the experiments available:
 - consumer: dummy1@Dummy experiments, dummy2@Dummy experiments
 - provider1: dummy1@Dummy experiments, dummy3@Dummy experiments
 - provider2: dummy1@Dummy experiments, dummy4@Dummy experiments

The relationships among the different actors will be:
 - consumer has different users: student1, student2, student3
 - consumer has a contract with provider1 to use its experiments (dummy1, dummy3, dummy4)
 - consumer does NOT have a contract with provider2

This basic environment will test the core federation functionality:
 - basic federation (student at consumer using dummy3)
 - distributed load balancing (student1 at consumer using dummy1 of consumer, and if it's busy, it will start using dummy1 at provider1)
 - subcontracting (student1@consume using dummy4 without having a direct contract with provider2)

This basic environment will not test policies, such as:
 - different priorities in the contracts
 - provider1 supporting dummy1 with local users and not with consumer users
 - etc.

