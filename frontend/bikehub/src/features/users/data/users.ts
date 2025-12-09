import { faker } from '@faker-js/faker'

// Set a fixed seed for consistent data generation
faker.seed(67890)

export const users = Array.from({ length: 500 }, () => {
  const firstName = faker.person.firstName()
  const lastName = faker.person.lastName()
  return {
    id: faker.string.uuid(),
    firstName,
    lastName,
    username: faker.internet
      .username({ firstName, lastName })
      .toLocaleLowerCase(),
    email: faker.internet.email({ firstName }).toLocaleLowerCase(),
    phoneNumber: faker.phone.number({ style: 'international' }),
    status: faker.helpers.arrayElement([
      '已激活',
      '未激活',
      // 'invited',
      '被暂停',
    ]),
    role: faker.helpers.arrayElement([
      '超级管理员',
      '管理员',
      '调度员',
    ]),
    last_login: faker.datatype.boolean()
      ? faker.date.past()
      : null,
    createdAt: faker.date.past(),
    updatedAt: faker.date.recent(),
  }
})
