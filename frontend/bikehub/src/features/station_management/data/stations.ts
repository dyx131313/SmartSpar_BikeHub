import { faker, fakerKU_ckb } from '@faker-js/faker'
import { stat } from 'fs'

// Set a fixed seed for consistent data generation
faker.seed(12345)

export const stations = Array.from({ length: 100 }, () => {
  const statuses = [
    'todo',
    'in progress',
    'done',
    'canceled',
    'backlog',
  ] as const
  const labels = ['bug', 'feature', 'documentation'] as const
  const priorities = ['low', 'medium', 'high'] as const
  const station_types = ['Docked', 'Dockless', 'Hybrid'] as const

  return {
    id: `${faker.number.int({ min: 1000, max: 9999 })}`,
    title: faker.lorem.sentence({ min: 5, max: 15 }),
    // name: faker.person.fullName(),
    name: `${faker.location.city()}, ${faker.location.country()}`,
    station_type: faker.helpers.arrayElement(station_types),
    latitude: Number(faker.location.latitude()),
    longitude: Number(faker.location.longitude()),
    capacity: faker.number.int({ min: 5, max: 50 }),
    description: faker.lorem.paragraph({ min: 1, max: 3 }),
    status: faker.helpers.arrayElement(statuses),
    label: faker.helpers.arrayElement(labels),
    // fuck_me : faker.lorem.sentence({ min: 5, max: 15 }),
    priority: faker.helpers.arrayElement(priorities),
    createdAt: faker.date.past(),
    updatedAt: faker.date.recent(),
    assignee: faker.person.fullName(),
    // description: faker.lorem.paragraph({ min: 1, max: 3 }),
    dueDate: faker.date.future(),
  }
})
