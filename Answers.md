
# Answers for Theoretical Questions

## Deployment on AWS

### Explain how you would deploy the above application on AWS.

There are multiple ways to deploy the Health Tracker application on AWS. Below is an approach I am most familiar with,
as it aligned well with my company's needs.
While I have limited hands-on experience with certain advanced deployment practices, I will outline them for
completeness.

1. **Deploying the Application on an EC2 Instance**<br>
   Launch an EC2 instance with the following configurations:
    - SSL/TLS certificate to enable HTTPS traffic.
    - Security group rules allowing inbound traffic on port 443 (HTTPS).
    - Database setup (for simplicity, a database can be hosted on the same instance,
      though a managed service like Amazon RDS would be a more scalable solution).
    - Domain name configuration to point to the EC2 instance for user-friendly access.
    - SSH access to the instance for remote management and troubleshooting.

2. **Implementing CI/CD for Automated Deployment (Best Practice, but not implemented in my current workflow)**
    - Set up a CI/CD pipeline to automate deployment using Jenkins, GitHub Actions, or AWS CodePipeline.
    - Optionally, containerize the application using Docker and deploy it as a containerized service.

3. **Load Balancing for Scalability (Best Practice, but not part of my current workflow)**
    - Deploy an AWS Application Load Balancer (ALB) to distribute traffic across multiple instances.
    - This ensures high availability and fault tolerance, preventing a single point of failure.

4. **Monitoring and Logging (Best Practice, but not implemented in my current workflow)**
    - Use AWS CloudWatch to monitor application performance, track API latency, and receive alerts for system failures.
    - Implement logging mechanisms to capture application logs for debugging and analytics.

5. **Database Backup Strategy (Best Practice, but not implemented in my current workflow)**
    - Use AWS Backup or Amazon RDS automated backups to periodically save database snapshots.
    - This ensures data recovery in case of failures or corruption.

6. **Running the API and Connecting to the Database**
    - Deploy the FastAPI application on the EC2 instance.
    - Configure database connections and verify successful data transactions.

7. **Testing and Verification**
    - Validate the deployment by running API tests in the AWS environment.
    - Ensure endpoints are accessible, secure, and functioning as expected.

____

## Scaling & Troubleshooting

As the application gains thousands of new users daily, issues such as inaccurate health scores,
slow API responses, and system crashes may arise. Each issue must be analyzed separately,
as multiple underlying factors could be contributing to these problems.

### 1. Diagnosing and Solving Current Issues

* Inaccurate Health Scores:
    - Verify the accuracy of the health score calculation algorithm.
    - Inspect the data sources and ensure consistency in data retrieval.
    - Assess whether the algorithm scales efficiently with large datasets.

* Slow API Responses:
    - Identify inefficient code or unoptimized queries affecting response times.
    - Introduce asynchronous processing to handle concurrent requests.
    - Evaluate server performance and determine if resource constraints exist.
    - Consider scaling up infrastructure (e.g., upgrading instance types or adding more instances).

* Application Crashes Under Load:
    - Check for memory leaks or resource exhaustion leading to instability.
    - Optimize database queries to reduce high-load operations.
    - Implement rate limiting to prevent excessive API requests from overwhelming the system.

There could also be a unifying issue causing all of these problems, such as a bottleneck in the database or a
misconfigured server.
such as bug in the health score calculation that cause the system to crash when it is called.

### 1. Long-Term Scalability Strategy

To make the system more resilient to future scalability challenges, the architecture should evolve beyond the current
monolithic design:

* Decouple Services:
    - Separate routing, database management, and business logic into individual microservices.
    - This allows independent scaling of different components, improving fault tolerance.

* Implement Horizontal Scaling:
    - Use AWS Auto Scaling to dynamically adjust the number of instances based on demand.
    - Deploy stateless services behind a load balancer for efficient request distribution.

* Adopt a More Robust Database Solution:
    - Migrate from database on server to Amazon RDS (PostgreSQL or MySQL) for better performance.
    - Use read replicas and caching mechanisms (e.g., Redis, AWS ElastiCache) to reduce database load.

* Enhance Fault Tolerance & Resilience:
    - Design the system so that failures in one component do not affect the entire application.
    - Implement graceful degradation, where essential services remain functional even if some parts fail.

By following these strategies, the application can scale efficiently, improve performance, and maintain reliability as
user demand grows.