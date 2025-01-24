"""
generate test data by using solution api post methods
1. clear existing data from db: user, solution, category, tag (use same .env config)
2. create admin user by post /api/users (auth server enable = false, allow any user to login)
3. post fake solutions one by one (category should be auto created, slug should be auto generated in backend)
"""
