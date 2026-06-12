# Beginner Explanatory Guide: PLATFORM-2950: Fix Prometheus Metric Cardinality Explosion

> **Task Type**: Product Task  
> **Domain/Focus**: Python Fundamentals, Metrics Collection

---

## 1. The Goal (In-Depth Beginner Explanation)

### The Core Problem
In the context of our application, we are facing a significant issue known as "cardinality explosion" in our metrics collection system. This problem arises when we include high-cardinality labels, such as user IDs, in our metrics. When each user ID is treated as a unique label, it leads to an overwhelming number of unique time series being generated. For instance, if we have 1 million users, each HTTP request tracked with a user ID creates a unique metric series. This results in an excessive amount of data being stored, which can fill up our Prometheus storage at an alarming rate of 2GB per hour. 

Fixing this issue is crucial because it not only affects the performance of our metrics storage but also impacts the observability of our application. If we do not address this, we risk losing the ability to monitor our application effectively, leading to potential downtimes and degraded user experiences. The goal of this task is to remove high-cardinality labels from our metrics, ensuring that we can still track important information without overwhelming our storage system.

### Jargon Buster (Key Terms Explained)
* **Cardinality**: In the context of metrics, cardinality refers to the uniqueness of data values. High cardinality means there are many unique values (like user IDs), which can lead to performance issues in data storage and retrieval. For example, if we track metrics for 1 million users, each user ID contributes to high cardinality.
  
* **Metrics**: Metrics are quantitative measurements used to assess the performance of a system. In our case, metrics help us understand how many HTTP requests are being made, their response times, and other performance indicators. For instance, tracking the number of requests to an API endpoint helps us gauge its usage and performance.

* **Prometheus**: Prometheus is an open-source monitoring and alerting toolkit widely used for recording real-time metrics in a time-series database. It allows developers to collect and query metrics data efficiently. For example, it can help visualize how many requests are made to a service over time.

* **Histogram**: A histogram is a type of metric that represents the distribution of a set of values. In our case, it is used to track the duration of HTTP requests. For example, we might want to know how many requests took less than 100ms, between 100ms and 500ms, etc.

### Expected Outcome
After implementing the solution, our metrics collection system should no longer include user IDs in the metric labels. This change will significantly reduce the number of unique time series generated, thus preventing cardinality explosion. 

**Before vs. After**:
- **Before**: Each HTTP request tracked with a user ID creates a unique metric series, leading to potentially millions of series and overwhelming storage.
- **After**: HTTP requests are tracked without user IDs, using aggregated counters instead, resulting in a manageable number of metric series that accurately reflect system performance without excessive storage use.

---

## 2. Related Coding Concepts & Syntax

### Concept 1: Functions and Parameters
#### 📘 Theoretical Overview (50%)
Functions are reusable blocks of code that perform a specific task. They can take inputs, known as parameters, and return outputs. Using functions helps organize code, making it easier to read, maintain, and debug. If we did not use functions, our code would become repetitive and harder to manage, leading to potential errors and inefficiencies.

Key mechanisms of functions include:
- **Parameters**: Variables that allow us to pass information into functions. For example, a function to calculate the area of a rectangle might take `width` and `height` as parameters.
- **Return Values**: The output that a function sends back after execution. For instance, a function that adds two numbers would return their sum.

#### 💻 Syntax & Practical Examples (50%)
* **Language Syntax**:
  ```python
  def function_name(parameter1, parameter2):
      # Function body
      return result
  ```

* **Real-World Application**:
  ```python
  def add_numbers(a, b):
      """Returns the sum of two numbers."""
      return a + b

  # Using the function
  result = add_numbers(5, 3)  # result is now 8
  ```

### Concept 2: Dictionaries
#### 📘 Theoretical Overview (50%)
Dictionaries are a built-in data type in Python that store data in key-value pairs. They are useful for organizing data that needs to be accessed by a unique key. If we did not use dictionaries, we would have to rely on lists or other structures, which could complicate data retrieval and management.

Key mechanisms of dictionaries include:
- **Key-Value Pairs**: Each entry in a dictionary consists of a key and its corresponding value. For example, in a dictionary representing a user, the key could be "name" and the value could be "Alice".
- **Accessing Values**: You can retrieve a value by referencing its key. For example, `user["name"]` would return "Alice".

#### 💻 Syntax & Practical Examples (50%)
* **Language Syntax**:
  ```python
  my_dict = {
      "key1": "value1",
      "key2": "value2"
  }
  ```

* **Real-World Application**:
  ```python
  user = {
      "name": "Alice",
      "age": 30,
      "email": "alice@example.com"
  }

  # Accessing a value
  print(user["name"])  # Output: Alice
  ```

---

## 3. Step-by-Step Logic & Walkthrough

1. **Step 1: Locate and Analyze the Target File**
   * Open the folder `p-w07-hotfix-01` and locate the file `metricsCollector.py`.
   * Focus on the `track_request` method, specifically the line where `user_id` is being used as a label in the `increment_counter` method.

2. **Step 2: Input Verification & Validation**
   * Check if the `user_id` parameter is being used correctly. Since we want to remove it, we need to ensure that the function can still operate without it.

3. **Step 3: Core Implementation / Modification**
   * Modify the `track_request` method to remove the `user_id` from the labels passed to `increment_counter`. Instead, we can just use the method, path, and status as labels.
   * Update the call to `increment_counter` to exclude `user_id`:
     ```python
     self.increment_counter('http_requests_total', {
         'method': method,
         'path': path,
         'status': str(status),
     })
     ```

4. **Step 4: Output Verification & Testing**
   * After making the changes, run the tests included at the bottom of the `metricsCollector.py` file.
   * Ensure that the assertion for the metric count passes, confirming that the cardinality is below the threshold.

---

## 4. Detailed Walkthrough of Test Cases

### Test Case 1: Standard / Success Case
* **Description**: This test checks the functionality of tracking HTTP requests without user IDs.
* **Inputs**:
  ```json
  {
      "method": "GET",
      "path": "/api/users",
      "status": 200,
      "duration": 0.05,
      "user_id": "user_1"
  }
  ```
* **Step-by-Step Execution Trace**:
  1. The `track_request` method receives the input values.
  2. The method constructs the labels without the `user_id`.
  3. The `increment_counter` method is called with the new labels.
  4. The metric count is updated, and the function completes successfully.
* **Expected Output**: The metric count should be less than 100, confirming that the cardinality has been reduced.

### Test Case 2: Edge Case / Validation Fail
* **Description**: This test checks the behavior when no valid HTTP request data is provided.
* **Inputs**:
  ```json
  {
      "method": "",
      "path": "",
      "status": 400,
      "duration": -1,
      "user_id": "user_1"
  }
  ```
* **Step-by-Step Execution Trace**:
  1. The `track_request` method receives the input values.
  2. The method detects that the `method` and `path` are empty, which is invalid.
  3. The execution is halted early, and an error is raised or a fallback value is returned.
* **Expected Output**: An error message indicating invalid input should be returned, preventing the creation of metrics with invalid data.