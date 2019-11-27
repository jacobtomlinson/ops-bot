# Gittter

A connector for [Gitter](https://developer.gitter.im/docs/welcome).

## Requirements

To use the Gitter connector you will need a user for the bot to use and generate a personal `token`. It is recommended that you create a separate user from your own account for this.

### Creating your application

- Create Gitter user for the bot to use and log into it
- Create a [token](https://developer.gitter.im/apps)
- Get the [room-id](https://developer.gitter.im/docs/rooms-resource) of room you want to listen.

## Configuration

```yaml
connectors:
  gitter:
    bot-name: "mr.boot" #optional
    room-id: "to be added" #required
    token: "to be added" #required
