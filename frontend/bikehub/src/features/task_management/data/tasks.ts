import { faker } from '@faker-js/faker'

// Set a fixed seed for consistent data generation
faker.seed(12345)

export const tasks = Array.from({ length: 100 }, () => {
  const statuses = [
    '待办',
    '正在进行',
    '已完成',
    '已取消',
    '积压',
  ] as const
  const labels = ['bug', 'feature', 'documentation'] as const
  const priorities = ['低', '中', '高', '紧急'] as const

  return {
    id: `TASK-${faker.number.int({ min: 1000, max: 9999 })}`,
    // title: faker.lorem.sentence({ min: 5, max: 15 }),
    from_station_id: faker.number.int({min: 1, max: 100}),
    to_station_id: faker.number.int({min: 1, max: 100}),
    bike_count: faker.number.int({min: 1, max: 100}),
    priority: faker.helpers.arrayElement(priorities),
    status: faker.helpers.arrayElement(statuses),
    assignee_id: faker.number.int({min: 1, max: 100}),
    creator_id: faker.number.int({min: 1, max: 100}),
    
    // label: faker.helpers.arrayElement(labels),
    // createdAt: faker.date.past()
    // updatedAt: faker.date.recent(),
    // assignee: faker.person.fullName(),
    // description: faker.lorem.paragraph({ min: 1, max: 3 }),
    // dueDate: faker.date.future(),
  }
})
