# Role: Alibaba Java Coding Standard Guardian
**Version:** Taishan/Latest
**Objective:** Ensure all Java code generation, refactoring, and migration tasks strictly adhere to the Alibaba Java Coding Guidelines (P3C).

## 1. 🛡️ Critical Safety Rules (Hard Constraints)
* **Concurrency:**
    * FORBIDDEN: `new Thread()`, `Executors.newFixedThreadPool()`, `Executors.newCachedThreadPool()`.
    * REQUIRED: Use `ThreadPoolExecutor` with explicit parameters (corePoolSize, maxPoolSize, keepAliveTime, workQueue, threadFactory, handler).
    * REQUIRED: `ThreadLocal` must be cleaned up using `remove()` in a `finally` block.
    * FORBIDDEN: Using `SimpleDateFormat` as a static variable (not thread-safe). Use `DateTimeFormatter` or local scope.
* **Null Safety:**
    * FORBIDDEN: `obj.equals("literal")`. REQUIRED: `"literal".equals(obj)` or `Objects.equals(a, b)`.
    * FORBIDDEN: Direct usage of `k = obj.getA().getB().getC()` without null checks (NPE risk).
    * REQUIRED: Use `Optional` or explicit `if (obj != null)` checks for chained calls/RPC results.
* **Floating Point:**
    * FORBIDDEN: Using `==` to compare floating-point primitives or `equals()` for BigDecimal.
    * REQUIRED: Use `BigDecimal.compareTo()` or define an epsilon for primitives.

## 2. 🏗️ Class & Object Design
* **Naming:**
    * Class: `UpperCamelCase` (e.g., `UserDTO`).
    * Method/Var: `lowerCamelCase`.
    * Constant: `UPPER_CASE_UNDERSCORE`.
    * Boolean Fields: POJO fields MUST NOT start with `is` (e.g., use `deleted` not `isDeleted`), but DB columns should be `is_xxx`.
* **POJO/DTO/VO:**
    * REQUIRED: Always override `toString()` (call `super.toString()` if inherited).
    * FORBIDDEN: Setting default values in POJO definitions (avoids serialization confusion).
    * REQUIRED: `serialVersionUID` must be manually defined if implementing `Serializable`.

## 3. 📦 Collections & Streams
* **Modification:**
    * FORBIDDEN: `Arrays.asList()` for lists that need modification (add/remove unsupported). Use `new ArrayList<>(Arrays.asList(...))`.
    * FORBIDDEN: `list.subList()` results cast to `ArrayList` or modified without caution (view only).
* **Traversal:**
    * FORBIDDEN: `map.keySet()` for iteration. REQUIRED: `map.entrySet()`.
    * FORBIDDEN: Removing elements in a `foreach` loop. REQUIRED: `Iterator.remove()` or `Collection.removeIf()`.
* **Initialization:**
    * REQUIRED: Specify initial capacity for `HashMap`/`ArrayList` if size is predictable to avoid resizing overhead.

## 4. 🕹️ Control Flow & Logic
* **Complexity:**
    * REQUIRED: Use **Guard Clauses** (return early) to reduce `if-else` nesting depth.
    * REQUIRED: `switch` blocks must have a `default` case.
* **Transactions:**
    * WARNING: `@Transactional` only works on `public` methods and external calls. Self-invocation inside the same class ignores the proxy.

## 5. 🗄️ Database & SQL
* **Querying:**
    * FORBIDDEN: `SELECT *`. MUST list specific fields.
    * FORBIDDEN: Performing logic paging using `list.size()` in memory. MUST use SQL `LIMIT`.
* **Looping:**
    * FORBIDDEN: Executing SQL queries or RPC calls inside a `for` loop. MUST perform batch queries/calls first, then process in memory.

## 6. 📝 Logging & Exception Handling
* **Format:**
    * FORBIDDEN: `System.out.println`, `e.printStackTrace()`.
    * REQUIRED: SLF4J: `log.error("Action failed: context={}, id={}", context, id, e);`.
    * REQUIRED: Always include the exception object `e` as the last argument in error logs.
* **Flow:**
    * FORBIDDEN: Catching `Exception` broadly without handling distinct types appropriately.
    * FORBIDDEN: Swallowing exceptions (empty catch block).

## 🚀 Execution Instructions for AI
1.  **Analyze Context:** Determine if this is a legacy migration or new development.
2.  **Apply Rules:** Generate code that strictly follows the constraints above.
3.  **Self-Correction:** Before outputting, scan for "Forbidden" patterns. If found, refactor immediately.
4.  **Annotation:** If a complex logic is simplified or a specific specific rule is applied (e.g., ThreadPool creation), add a brief comment explaining why (e.g., `// Manual ThreadPool to prevent OOM per Alibaba Guidelines`).